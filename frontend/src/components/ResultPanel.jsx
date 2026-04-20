function formatDetailValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => (typeof item === "object" ? JSON.stringify(item) : String(item))).join(", ");
  }

  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export default function ResultPanel({ selectedTask, formatTimestamp }) {
  return (
    <section className="panel">
      <h2>Result</h2>
      {selectedTask ? (
        <div className="result-stack">
          <div>
            <span className="label">Task</span>
            <p>{selectedTask.task}</p>
          </div>
          <div>
            <span className="label">Selected Tool</span>
            <p>{selectedTask.selected_tool}</p>
          </div>
          <div>
            <span className="label">Output</span>
            <p>{selectedTask.final_output}</p>
          </div>
          <div>
            <span className="label">Timestamp</span>
            <p>{formatTimestamp(selectedTask.timestamp)}</p>
          </div>
          <div>
            <span className="label">Trace</span>
            <ol className="trace-list">
              {selectedTask.execution_steps.map((step, index) => (
                <li key={`${step.stage}-${index}`}>
                  <strong>{step.stage}</strong>
                  <span>{step.message}</span>
                  {Object.keys(step.details || {}).length ? (
                    <div className="trace-details">
                      {Object.entries(step.details).map(([key, value]) => (
                        <p key={key}>
                          <span>{key}: </span>
                          {formatDetailValue(value)}
                        </p>
                      ))}
                    </div>
                  ) : null}
                </li>
              ))}
            </ol>
          </div>
        </div>
      ) : (
        <p className="muted">Submit a task to see the trace and output.</p>
      )}
    </section>
  );
}
