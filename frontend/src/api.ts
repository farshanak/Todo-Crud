export type Priority = "low" | "medium" | "high" | "urgent";

export interface Todo {
  id: number;
  title: string;
  done: boolean;
  due_at?: string | null;
  priority?: Priority;
}

export interface TodoInput {
  title: string;
  done: boolean;
  due_at?: string | null;
  priority?: Priority;
}

export interface TodoFilters {
  q?: string;
  priority?: Priority;
  overdue?: boolean;
}

export function createApi(baseUrl: string) {
  if (!baseUrl) {
    throw new Error("API base URL is required");
  }

  async function fetchTodos(filters: TodoFilters = {}): Promise<Todo[]> {
    const params = new URLSearchParams();
    if (filters.q) params.set("q", filters.q);
    if (filters.priority) params.set("priority", filters.priority);
    if (filters.overdue) params.set("overdue", "true");
    const qs = params.toString();
    const res = await fetch(`${baseUrl}/todos${qs ? `?${qs}` : ""}`);
    if (!res.ok) throw new Error("Failed to fetch todos");
    return res.json();
  }

  async function createTodo(
    title: string,
    extras: { due_at?: string | null; priority?: Priority } = {},
  ): Promise<Todo> {
    const body: TodoInput = { title, done: false, ...extras };
    const res = await fetch(`${baseUrl}/todos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("Failed to create todo");
    return res.json();
  }

  async function updateTodo(todo: Todo): Promise<Todo> {
    const body: TodoInput = { title: todo.title, done: todo.done };
    if (todo.due_at !== undefined) body.due_at = todo.due_at;
    if (todo.priority !== undefined) body.priority = todo.priority;
    const res = await fetch(`${baseUrl}/todos/${todo.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("Failed to update todo");
    return res.json();
  }

  async function deleteTodo(id: number): Promise<void> {
    const res = await fetch(`${baseUrl}/todos/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete todo");
  }

  return { fetchTodos, createTodo, updateTodo, deleteTodo };
}
