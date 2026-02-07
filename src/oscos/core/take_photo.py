import cv2
import numpy as np
from pypylon import pylon


def take_photo(exposure_us=2000000, gain_db=0.0):
    """
    Captura imagen con cámara Basler y regresa:
    - color_bgr: imagen en color
    - gray: imagen en blanco y negro
    """

    tlf = pylon.TlFactory.GetInstance()
    devices = tlf.EnumerateDevices()

    if not devices:
        raise RuntimeError("No se encontró cámara Basler.")

    cam = pylon.InstantCamera(tlf.CreateDevice(devices[0]))
    cam.Open()

    # Pixel Formats a intentar
    for fmt in ["RGB8", "BGR8", "BayerRG8", "BayerGB8", "BayerBG8", "BayerGR8"]:
        try:
            cam.PixelFormat.SetValue(fmt)
            break
        except:
            continue

    # Desactivar auto
    if hasattr(cam, "GainAuto"):
        cam.GainAuto.SetValue("Off")
    if hasattr(cam, "ExposureAuto"):
        cam.ExposureAuto.SetValue("Off")

    # Configuración de exposición y ganancia
    cam.Gain.SetValue(gain_db)
    cam.ExposureTime.SetValue(exposure_us)

    # Ajuste de resolución completa
    cam.Width.SetValue(2040)
    cam.Height.SetValue(1086)
    cam.OffsetX.SetValue(0)
    cam.OffsetY.SetValue(0)

    cam.TriggerMode.SetValue("Off")

    # Captura
    cam.StartGrabbing(1)
    grab = cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if not grab.GrabSucceeded():
        cam.Close()
        raise RuntimeError("Falló la captura.")

    raw = grab.GetArray().copy()
    grab.Release()
    cam.Close()

    # Si es Bayer, demosaicing
    if len(raw.shape) == 2:
        try:
            color_bgr = cv2.cvtColor(raw, cv2.COLOR_BayerRG2BGR)
        except:
            raise RuntimeError("Error en demosaicing.")
    else:
        color_bgr = raw

    # Aplicar balance de color (multiplicadores por canal)
    # Los valores pedidos vienen en formato RGB; OpenCV usa BGR.
    # Valores: red 1,06445  -> 1.06445
    #         green 0,87891 -> 0.87891
    #         blue 1,06787  -> 1.06787
    r_mult = 0.952
    g_mult = 0.95
    b_mult = 1

    try:
        img_f = color_bgr.astype(np.float32)
        img_f[..., 0] *= b_mult
        img_f[..., 1] *= g_mult
        img_f[..., 2] *= r_mult
        img_f = np.clip(img_f, 0, 255)
        color_bgr = img_f.astype(np.uint8)
    except Exception:
        # Fallback: leave image unchanged on any unexpected issue
        pass

    # Convertir a gris
    gray = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2GRAY)

    return color_bgr


if __name__ == "__main__":
    # Quick test: try to take one photo and save it to disk.
    import time
    out_name = f"test_capture_{time.strftime('%Y%m%d_%H%M%S')}.png"
    try:
        img = take_photo()
    except Exception as e:
        print("take_photo failed:", e)
        print("If you don't have a Basler camera available this test will fail.")
    else:
        try:
            import cv2
            ok = cv2.imwrite(out_name, img)
            if ok:
                print("Saved test image to", out_name)
            else:
                print("Failed to write image to disk")
        except Exception as e:
            print("Saving image failed:", e)
