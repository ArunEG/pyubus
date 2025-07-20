#
# Copyright (C) 2025 OpenWrt.org
#
# This is free software, licensed under the MIT License.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=python3-pyubus
PKG_VERSION:=1.0.0
PKG_RELEASE:=1

PKG_SOURCE:=pyubus-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/ArunEG/pyubus/archive/v$(PKG_VERSION)/
PKG_HASH:=skip

PKG_MAINTAINER:=PyUbus Contributors
PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=LICENSE

PKG_BUILD_DIR:=$(BUILD_DIR)/pyubus-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk
include $(TOPDIR)/feeds/packages/lang/python/python3-package.mk

define Package/python3-pyubus
  SUBMENU:=Python
  SECTION:=lang
  CATEGORY:=Languages
  TITLE:=Python interface for OpenWrt ubus
  URL:=https://github.com/ArunEG/pyubus
  DEPENDS:=+python3-light +python3-urllib3 +python3-certifi +python3-requests
  VARIANT:=python3
endef

define Package/python3-pyubus/description
  PyUbus provides a comprehensive Python interface for interacting with 
  OpenWrt's ubus (micro bus architecture) via HTTP/JSON-RPC. This package 
  replaces the need for subprocess calls to the ubus command-line tool 
  with a clean, Pythonic API that supports session management, error 
  handling, and includes a CLI tool.
endef

define Package/python3-pyubus/conffiles
/etc/config/pyubus
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) $(BUILD_DIR)/../../pyubus/* $(PKG_BUILD_DIR)/
	$(CP) $(BUILD_DIR)/../../setup.py $(PKG_BUILD_DIR)/
	$(CP) $(BUILD_DIR)/../../README.md $(PKG_BUILD_DIR)/
	$(CP) $(BUILD_DIR)/../../LICENSE $(PKG_BUILD_DIR)/
	$(CP) $(BUILD_DIR)/../../requirements.txt $(PKG_BUILD_DIR)/
endef

define Build/Compile
	$(call Py3Build/Compile/Default)
	
	# Build native C extension if dependencies are available
	if [ -f "$(PKG_BUILD_DIR)/pyubus/c_extension/ubus_module.c" ]; then \
		echo "Building native C extension..."; \
		cd $(PKG_BUILD_DIR)/pyubus/c_extension && \
		$(STAGING_DIR_HOST)/bin/python3 setup.py build_ext --inplace \
			--include-dirs="$(STAGING_DIR)/usr/include" \
			--library-dirs="$(STAGING_DIR)/usr/lib" || \
		echo "C extension build failed, continuing without native acceleration"; \
	fi
endef

define Py3Package/python3-pyubus/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/pyubus $(1)/usr/bin/
	
	# Install native C extension if it was built
	if [ -f "$(PKG_BUILD_DIR)/pyubus/c_extension/ubus_native"*.so ]; then \
		echo "Installing native C extension..."; \
		$(INSTALL_DIR) $(1)$(PYTHON3_PKG_DIR); \
		$(CP) $(PKG_BUILD_DIR)/pyubus/c_extension/ubus_native*.so $(1)$(PYTHON3_PKG_DIR)/; \
	fi
	
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_CONF) ./files/pyubus.config $(1)/etc/config/pyubus
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/pyubus.init $(1)/etc/init.d/pyubus
	
	# Install documentation
	$(INSTALL_DIR) $(1)/usr/share/doc/python3-pyubus
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/NATIVE_UBUS_GUIDE.md $(1)/usr/share/doc/python3-pyubus/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/INSTALL_OPENWRT.md $(1)/usr/share/doc/python3-pyubus/
endef

$(eval $(call Py3Package,python3-pyubus))
$(eval $(call BuildPackage,python3-pyubus))
$(eval $(call BuildPackage,python3-pyubus-src)) 