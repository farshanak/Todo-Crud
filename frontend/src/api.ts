export interface Todo {
  id: number;
  title: string;
  done: boolean;
}

export interface TodoInput {
  title: string;
  done: boolean;
}

export function createApi(baseUrl: string) {
  if (!baseUrl) {
    throw new Error("API base URL is required");
  }

  async function fetchTodos(): Promise<Todo[]> {
    const res = await fetch(`${baseUrl}/todos`);
    if (!res.ok) throw new Error("Failed to fetch todos");
    return res.json();
  }

  async function createTodo(title: string): Promise<Todo> {
    const res = await fetch(`${baseUrl}/todos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, done: false }),
    });
    if (!res.ok) throw new Error("Failed to create todo");
    return res.json();
  }

  async function updateTodo(todo: Todo): Promise<Todo> {
    const res = await fetch(`${baseUrl}/todos/${todo.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: todo.title, done: todo.done } satisfies TodoInput),
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
