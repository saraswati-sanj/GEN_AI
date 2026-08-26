/**
 * NutriLens AI — Camera Stream Barcode Scanner Module
 * Integrates ZXing browser code reader to scan live camera feed for EAN/UPC barcodes.
 */
class BarcodeScanner {
  constructor() {
    this.codeReader = null;
    this.selectedDeviceId = null;
    this.isScanning = false;
    this.onBarcodeFoundCallback = null;
  }

  init() {
    if (typeof ZXing !== "undefined") {
      this.codeReader = new ZXing.BrowserMultiFormatReader();
      console.log("ZXing Barcode Reader initialized.");
    } else {
      console.warn("ZXing library not loaded yet.");
    }
  }

  async startCamera(videoElementId, onFoundCallback) {
    if (!this.codeReader) {
      this.init();
    }
    if (!this.codeReader) {
      throw new Error("Barcode scanner library could not be loaded.");
    }

    this.onBarcodeFoundCallback = onFoundCallback;
    this.isScanning = true;

    try {
      const videoInputDevices = await this.codeReader.listVideoInputDevices();
      if (!videoInputDevices || videoInputDevices.length === 0) {
        throw new Error("No video input camera devices found on your system.");
      }

      // Select environment / back camera if available
      const backCamera = videoInputDevices.find(dev => 
        dev.label.toLowerCase().includes("back") || dev.label.toLowerCase().includes("rear") || dev.label.toLowerCase().includes("environment")
      );
      this.selectedDeviceId = backCamera ? backCamera.deviceId : videoInputDevices[0].deviceId;

      console.log("Starting camera decode on device:", this.selectedDeviceId);

      this.codeReader.decodeFromVideoDevice(
        this.selectedDeviceId,
        videoElementId,
        (result, err) => {
          if (result && this.isScanning) {
            const barcodeText = result.getText();
            console.log("Barcode detected in camera stream:", barcodeText);
            if (this.onBarcodeFoundCallback) {
              this.onBarcodeFoundCallback(barcodeText);
            }
          }
        }
      );

      return true;
    } catch (err) {
      console.error("Camera access error:", err);
      this.isScanning = false;
      throw err;
    }
  }

  stopCamera() {
    if (this.codeReader && this.isScanning) {
      this.codeReader.reset();
      this.isScanning = false;
      console.log("Camera scanner stopped.");
    }
  }
}

window.barcodeScanner = new BarcodeScanner();
