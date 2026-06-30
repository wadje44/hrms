export interface GeoResult {
  available: boolean;
  lat: number | null;
  lng: number | null;
  error?: string;
}

/**
 * Request the current GPS position. Resolves with available=false on
 * permission denial or unavailability (doc §9.1) — never rejects.
 */
export function getPosition(timeoutMs = 10000): Promise<GeoResult> {
  return new Promise((resolve) => {
    if (!("geolocation" in navigator)) {
      resolve({ available: false, lat: null, lng: null, error: "Geolocation unsupported" });
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({
          available: true,
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        }),
      (err) => resolve({ available: false, lat: null, lng: null, error: err.message }),
      { enableHighAccuracy: true, timeout: timeoutMs, maximumAge: 0 },
    );
  });
}
