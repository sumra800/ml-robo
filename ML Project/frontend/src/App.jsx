import { useEffect, useRef, useState } from "react";
import { detectFromBase64, detectFromFile, healthCheck } from "./api";
import DetectionResult from "./components/DetectionResult";

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [apiStatus, setApiStatus] = useState("Checking...");
  const [selectedImageUrl, setSelectedImageUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);

  useEffect(() => {
    healthCheck()
      .then((data) =>
        setApiStatus(
          data.model_ready ? "API online (model ready)" : `API degraded: ${data.message}`
        )
      )
      .catch(() => setApiStatus("API offline"));
  }, []);

  const onUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedImageUrl(URL.createObjectURL(file));
    setError("");
    setLoading(true);
    try {
      const data = await detectFromFile(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraOn(true);
    } catch {
      setError("Unable to access camera");
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    setCameraOn(false);
  };

  const detectFromCamera = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    setError("");
    setLoading(true);
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg");
    setSelectedImageUrl(dataUrl);

    try {
      const data = await detectFromBase64(dataUrl);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>AI Waste Sorting Dashboard</h1>
      <p className="status">{apiStatus}</p>

      <div className="panel">
        <h2>Upload Image</h2>
        <input type="file" accept="image/*" onChange={onUpload} />
      </div>

      <div className="panel">
        <h2>Webcam</h2>
        <div className="row">
          {!cameraOn ? (
            <button onClick={startCamera}>Start Camera</button>
          ) : (
            <button onClick={stopCamera}>Stop Camera</button>
          )}
          <button disabled={!cameraOn || loading} onClick={detectFromCamera}>
            Detect Current Frame
          </button>
        </div>
        <video ref={videoRef} autoPlay playsInline className="video" />
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {selectedImageUrl ? (
        <div className="panel">
          <h2>Input Preview</h2>
          <img src={selectedImageUrl} alt="Selected waste" className="preview" />
        </div>
      ) : null}

      {loading ? <p>Running detection...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <DetectionResult data={result} />
    </div>
  );
}

export default App;
