const API_BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

export function createTask(task) {
  return request("/tasks", {
    method: "POST",
    body: JSON.stringify({ task }),
  });
}

export function fetchTasks() {
  return request("/tasks");
}

export function fetchTask(id) {
  return request(`/tasks/${id}`);
}
