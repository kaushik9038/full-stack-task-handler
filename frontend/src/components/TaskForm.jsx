export default function TaskForm({ task, setTask, onSubmit, isSubmitting, error }) {
  return (
    <section className="panel">
      <h2>New Task</h2>
      <form onSubmit={onSubmit} className="task-form">
        <textarea
          value={task}
          onChange={(event) => setTask(event.target.value)}
          placeholder='Try "uppercase hello world" or "weather in Edmonton"'
          rows={5}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Running..." : "Submit"}
        </button>
      </form>
      {error ? (
        <div className="error">
          <strong>{error.title}</strong>
          <p>{error.message}</p>
        </div>
      ) : null}
    </section>
  );
}
