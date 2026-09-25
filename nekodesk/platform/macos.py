def apply_macos_tweaks(window_id) -> None:
    # Attempt to set macOS application activation policy to Accessory (2)
    # which hides the Dock icon and keeps the app in the background.
    try:
        import ctypes
        # Load AppKit and ObjC runtimes
        appkit = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/AppKit.framework/AppKit')
        objc = ctypes.cdll.LoadLibrary('/usr/lib/libobjc.A.dylib')
        
        # Setup signatures
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        
        # Send message signatures
        # On x86_64 and arm64, objc_msgSend has a standard calling convention
        objc_msgSend = objc.objc_msgSend
        objc_msgSend.restype = ctypes.c_void_p
        objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        
        # 1. Get NSApplication class
        cls_nsapp = objc.objc_getClass(b"NSApplication")
        sel_sharedapp = objc.sel_registerName(b"sharedApplication")
        
        # NSApp = [NSApplication sharedApplication]
        ns_app = objc_msgSend(cls_nsapp, sel_sharedapp)
        
        if ns_app:
            # 2. [ns_app setActivationPolicy:2] (NSApplicationActivationPolicyAccessory = 2)
            sel_setpolicy = objc.sel_registerName(b"setActivationPolicy:")
            
            # Since setActivationPolicy: takes an NSInteger (long), we need to cast msgSend
            objc_msgSend_long = objc.objc_msgSend
            objc_msgSend_long.restype = ctypes.c_void_p
            objc_msgSend_long.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
            
            # Apply policy change
            objc_msgSend_long(ns_app, sel_setpolicy, 2)
            print("Successfully set macOS activation policy to accessory (hid dock icon).")
    except Exception as e:
        # Fall back silently if ctypes or Mac framework loading fails
        print(f"macOS dynamic dock hide fallback: {e}")
