export default function DetectionResult({ data }) {
  if (!data) return null;

  return (
    <div className="panel">
      <h2>Detections</h2>
      {data.detections.length === 0 ? (
        <p>No objects detected.</p>
      ) : (
        <ul className="detection-list">
          {data.detections.map((det, idx) => (
            <li key={`${det.class_name}-${idx}`} className="detection-item">
              <strong>{det.class_name}</strong> ({(det.confidence * 100).toFixed(1)}%)
              <div>Recommended Bin: {det.recommended_bin}</div>
              <div>Action: {det.action}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
