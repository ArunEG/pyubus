/*
 * Python C extension for direct libubus communication
 * 
 * This module provides Python bindings for libubus, allowing direct
 * communication with ubusd without HTTP/JSON-RPC overhead.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <libubus.h>
#include <json-c/json.h>
#include <structmember.h>

/* UbusClient object structure */
typedef struct {
    PyObject_HEAD
    struct ubus_context *ctx;
    int connected;
    int timeout;
} UbusClientObject;

/* Forward declarations */
static PyTypeObject UbusClientType;

/* Convert JSON object to Python object */
static PyObject *json_to_python(json_object *obj) {
    if (!obj) {
        Py_RETURN_NONE;
    }
    
    enum json_type type = json_object_get_type(obj);
    
    switch (type) {
        case json_type_boolean:
            return PyBool_FromLong(json_object_get_boolean(obj));
            
        case json_type_int:
            return PyLong_FromLongLong(json_object_get_int64(obj));
            
        case json_type_double:
            return PyFloat_FromDouble(json_object_get_double(obj));
            
        case json_type_string:
            return PyUnicode_FromString(json_object_get_string(obj));
            
        case json_type_array: {
            int len = json_object_array_length(obj);
            PyObject *list = PyList_New(len);
            if (!list) return NULL;
            
            for (int i = 0; i < len; i++) {
                json_object *item = json_object_array_get_idx(obj, i);
                PyObject *py_item = json_to_python(item);
                if (!py_item) {
                    Py_DECREF(list);
                    return NULL;
                }
                PyList_SetItem(list, i, py_item);
            }
            return list;
        }
        
        case json_type_object: {
            PyObject *dict = PyDict_New();
            if (!dict) return NULL;
            
            json_object_object_foreach(obj, key, val) {
                PyObject *py_key = PyUnicode_FromString(key);
                PyObject *py_val = json_to_python(val);
                
                if (!py_key || !py_val) {
                    Py_XDECREF(py_key);
                    Py_XDECREF(py_val);
                    Py_DECREF(dict);
                    return NULL;
                }
                
                PyDict_SetItem(dict, py_key, py_val);
                Py_DECREF(py_key);
                Py_DECREF(py_val);
            }
            return dict;
        }
        
        default:
            Py_RETURN_NONE;
    }
}

/* Convert Python object to JSON object */
static json_object *python_to_json(PyObject *obj) {
    if (obj == Py_None) {
        return NULL;
    }
    
    if (PyBool_Check(obj)) {
        return json_object_new_boolean(obj == Py_True);
    }
    
    if (PyLong_Check(obj)) {
        return json_object_new_int64(PyLong_AsLongLong(obj));
    }
    
    if (PyFloat_Check(obj)) {
        return json_object_new_double(PyFloat_AsDouble(obj));
    }
    
    if (PyUnicode_Check(obj)) {
        return json_object_new_string(PyUnicode_AsUTF8(obj));
    }
    
    if (PyList_Check(obj) || PyTuple_Check(obj)) {
        Py_ssize_t len = PySequence_Length(obj);
        json_object *arr = json_object_new_array();
        
        for (Py_ssize_t i = 0; i < len; i++) {
            PyObject *item = PySequence_GetItem(obj, i);
            json_object *json_item = python_to_json(item);
            Py_DECREF(item);
            
            if (json_item) {
                json_object_array_add(arr, json_item);
            }
        }
        return arr;
    }
    
    if (PyDict_Check(obj)) {
        json_object *dict = json_object_new_object();
        PyObject *key, *value;
        Py_ssize_t pos = 0;
        
        while (PyDict_Next(obj, &pos, &key, &value)) {
            if (PyUnicode_Check(key)) {
                const char *key_str = PyUnicode_AsUTF8(key);
                json_object *json_val = python_to_json(value);
                
                if (json_val) {
                    json_object_object_add(dict, key_str, json_val);
                }
            }
        }
        return dict;
    }
    
    return NULL;
}

/* Callback for ubus method calls */
static void call_cb(struct ubus_request *req, int type, struct blob_attr *msg) {
    PyObject **result = (PyObject **)req->priv;
    
    if (msg) {
        char *json_str = blobmsg_format_json(msg, true);
        if (json_str) {
            json_object *json_obj = json_tokener_parse(json_str);
            if (json_obj) {
                *result = json_to_python(json_obj);
                json_object_put(json_obj);
            }
            free(json_str);
        }
    }
    
    if (!*result) {
        *result = PyDict_New();
    }
}

/* UbusClient.__init__ */
static int UbusClient_init(UbusClientObject *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"timeout", NULL};
    
    self->timeout = 30;
    self->connected = 0;
    self->ctx = NULL;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &self->timeout)) {
        return -1;
    }
    
    return 0;
}

/* UbusClient.__dealloc__ */
static void UbusClient_dealloc(UbusClientObject *self) {
    if (self->ctx) {
        ubus_free(self->ctx);
        self->ctx = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* UbusClient.connect() */
static PyObject *UbusClient_connect(UbusClientObject *self, PyObject *args) {
    const char *socket_path = NULL;
    
    if (!PyArg_ParseTuple(args, "|s", &socket_path)) {
        return NULL;
    }
    
    if (self->connected) {
        Py_RETURN_NONE;
    }
    
    self->ctx = ubus_connect(socket_path);
    if (!self->ctx) {
        PyErr_SetString(PyExc_ConnectionError, "Failed to connect to ubus");
        return NULL;
    }
    
    self->connected = 1;
    Py_RETURN_NONE;
}

/* UbusClient.disconnect() */
static PyObject *UbusClient_disconnect(UbusClientObject *self, PyObject *args) {
    if (self->ctx) {
        ubus_free(self->ctx);
        self->ctx = NULL;
        self->connected = 0;
    }
    Py_RETURN_NONE;
}

/* UbusClient.list() */
static PyObject *UbusClient_list(UbusClientObject *self, PyObject *args) {
    const char *path = NULL;
    
    if (!PyArg_ParseTuple(args, "|s", &path)) {
        return NULL;
    }
    
    if (!self->connected) {
        PyErr_SetString(PyExc_RuntimeError, "Not connected to ubus");
        return NULL;
    }
    
    PyObject *result = NULL;
    struct ubus_request req;
    
    int ret = ubus_lookup(self->ctx, path, call_cb, &result);
    
    if (ret != UBUS_STATUS_OK) {
        PyErr_Format(PyExc_RuntimeError, "ubus lookup failed: %d", ret);
        return NULL;
    }
    
    if (!result) {
        result = PyDict_New();
    }
    
    return result;
}

/* UbusClient.call() */
static PyObject *UbusClient_call(UbusClientObject *self, PyObject *args, PyObject *kwargs) {
    const char *object_name, *method;
    PyObject *params = NULL;
    
    static char *kwlist[] = {"object", "method", "params", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss|O", kwlist, 
                                   &object_name, &method, &params)) {
        return NULL;
    }
    
    if (!self->connected) {
        PyErr_SetString(PyExc_RuntimeError, "Not connected to ubus");
        return NULL;
    }
    
    // Look up object ID
    uint32_t obj_id;
    int ret = ubus_lookup_id(self->ctx, object_name, &obj_id);
    if (ret != UBUS_STATUS_OK) {
        PyErr_Format(PyExc_RuntimeError, "Object '%s' not found: %d", object_name, ret);
        return NULL;
    }
    
    // Prepare parameters
    struct blob_buf b = {0};
    blob_buf_init(&b, 0);
    
    if (params && params != Py_None) {
        json_object *json_params = python_to_json(params);
        if (json_params) {
            const char *json_str = json_object_to_json_string(json_params);
            if (json_str) {
                // Convert JSON to blobmsg format
                if (!blobmsg_add_json_from_string(&b, json_str)) {
                    json_object_put(json_params);
                    blob_buf_free(&b);
                    PyErr_SetString(PyExc_ValueError, "Failed to convert parameters");
                    return NULL;
                }
            }
            json_object_put(json_params);
        }
    }
    
    // Make the call
    PyObject *result = NULL;
    ret = ubus_invoke(self->ctx, obj_id, method, b.head, call_cb, &result, self->timeout * 1000);
    
    blob_buf_free(&b);
    
    if (ret != UBUS_STATUS_OK) {
        const char *error_msg = "Unknown error";
        switch (ret) {
            case UBUS_STATUS_INVALID_COMMAND:
                error_msg = "Invalid command";
                break;
            case UBUS_STATUS_INVALID_ARGUMENT:
                error_msg = "Invalid argument";
                break;
            case UBUS_STATUS_METHOD_NOT_FOUND:
                error_msg = "Method not found";
                break;
            case UBUS_STATUS_NOT_FOUND:
                error_msg = "Object not found";
                break;
            case UBUS_STATUS_PERMISSION_DENIED:
                error_msg = "Permission denied";
                break;
            case UBUS_STATUS_TIMEOUT:
                error_msg = "Timeout";
                break;
        }
        
        PyErr_Format(PyExc_RuntimeError, "ubus call failed: %s (%d)", error_msg, ret);
        Py_XDECREF(result);
        return NULL;
    }
    
    if (!result) {
        result = PyDict_New();
    }
    
    return result;
}

/* UbusClient methods table */
static PyMethodDef UbusClient_methods[] = {
    {"connect", (PyCFunction)UbusClient_connect, METH_VARARGS,
     "Connect to ubus daemon"},
    {"disconnect", (PyCFunction)UbusClient_disconnect, METH_NOARGS,
     "Disconnect from ubus daemon"},
    {"list", (PyCFunction)UbusClient_list, METH_VARARGS,
     "List ubus objects"},
    {"call", (PyCFunction)UbusClient_call, METH_VARARGS | METH_KEYWORDS,
     "Call ubus method"},
    {NULL}  /* Sentinel */
};

/* UbusClient members table */
static PyMemberDef UbusClient_members[] = {
    {"timeout", T_INT, offsetof(UbusClientObject, timeout), 0,
     "Timeout for ubus calls"},
    {"connected", T_BOOL, offsetof(UbusClientObject, connected), READONLY,
     "Connection status"},
    {NULL}  /* Sentinel */
};

/* UbusClient type definition */
static PyTypeObject UbusClientType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "ubus_native.UbusClient",
    .tp_doc = "Native ubus client using libubus",
    .tp_basicsize = sizeof(UbusClientObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)UbusClient_init,
    .tp_dealloc = (destructor)UbusClient_dealloc,
    .tp_methods = UbusClient_methods,
    .tp_members = UbusClient_members,
};

/* Module definition */
static PyModuleDef ubus_native_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "ubus_native",
    .m_doc = "Native Python bindings for libubus",
    .m_size = -1,
};

/* Module initialization */
PyMODINIT_FUNC PyInit_ubus_native(void) {
    PyObject *m;

    if (PyType_Ready(&UbusClientType) < 0)
        return NULL;

    m = PyModule_Create(&ubus_native_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&UbusClientType);
    if (PyModule_AddObject(m, "UbusClient", (PyObject *)&UbusClientType) < 0) {
        Py_DECREF(&UbusClientType);
        Py_DECREF(m);
        return NULL;
    }
    
    /* Add status constants */
    PyModule_AddIntConstant(m, "UBUS_STATUS_OK", UBUS_STATUS_OK);
    PyModule_AddIntConstant(m, "UBUS_STATUS_INVALID_COMMAND", UBUS_STATUS_INVALID_COMMAND);
    PyModule_AddIntConstant(m, "UBUS_STATUS_INVALID_ARGUMENT", UBUS_STATUS_INVALID_ARGUMENT);
    PyModule_AddIntConstant(m, "UBUS_STATUS_METHOD_NOT_FOUND", UBUS_STATUS_METHOD_NOT_FOUND);
    PyModule_AddIntConstant(m, "UBUS_STATUS_NOT_FOUND", UBUS_STATUS_NOT_FOUND);
    PyModule_AddIntConstant(m, "UBUS_STATUS_NO_DATA", UBUS_STATUS_NO_DATA);
    PyModule_AddIntConstant(m, "UBUS_STATUS_PERMISSION_DENIED", UBUS_STATUS_PERMISSION_DENIED);
    PyModule_AddIntConstant(m, "UBUS_STATUS_TIMEOUT", UBUS_STATUS_TIMEOUT);

    return m;
} 