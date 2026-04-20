export default function HistoryPanel({ tasks, selectedTask, onSelect, formatTimestamp }) {
  return (
    <section className="panel history-panel">
      <h2>History</h2>
      {tasks.length ? (
        <ul className="history-list">
          {tasks.map((taskItem) => (
            <li key={taskItem.id}>
              <button
                type="button"
                className={taskItem.id === selectedTask?.id ? "history-item active" : "history-item"}
                onClick={() => onSelect(taskItem.id)}
              >
                <span className="history-task">{taskItem.task}</span>
                <span className="history-meta">
                  {taskItem.selected_tool} • {formatTimestamp(taskItem.timestamp)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No tasks yet.</p>
      )}
    </section>
  );
}
