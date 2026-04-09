interface Todo {
  id: number;
  title: string;
  done: boolean;
}

const API = "http://localhost:8000";

const listEl = document.getElementById("todo-list") as HTMLUListElement;
const formEl = document.getElementById("new-todo-form") as HTMLFormElement;
const inputEl = document.getElementById("new-todo-input") as HTMLInputElement;

async function fetchTodos(): Promise<Todo[]> {
  const res = await fetch(`${API}/todos`);
  if (!res.ok) throw new Error("Failed to fetch todos");
  return res.json();
}

async function createTodo(title: string): Promise<Todo> {
  const res = await fetch(`${API}/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, done: false }),
  });
  if (!res.ok) throw new Error("Failed to create todo");
  return res.json();
}

async function updateTodo(todo: Todo): Promise<Todo> {
  const res = await fetch(`${API}/todos/${todo.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: todo.title, done: todo.done }),
  });
  if (!res.ok) throw new Error("Failed to update todo");
  return res.json();
}

async function deleteTodo(id: number): Promise<void> {
  const res = await fetch(`${API}/todos/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete todo");
}

function render(todos: Todo[]): void {
  listEl.innerHTML = "";
  for (const todo of todos) {
    const li = document.createElement("li");
    if (todo.done) li.classList.add("done");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.done;
    checkbox.addEventListener("change", async () => {
      await updateTodo({ ...todo, done: checkbox.checked });
      await refresh();
    });

    const title = document.createElement("span");
    title.textContent = todo.title;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Delete";
    removeBtn.addEventListener("click", async () => {
      await deleteTodo(todo.id);
      await refresh();
    });

    li.append(checkbox, title, removeBtn);
    listEl.appendChild(li);
  }
}

async function refresh(): Promise<void> {
  const todos = await fetchTodos();
  render(todos);
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = inputEl.value.trim();
  if (!title) return;
  await createTodo(title);
  inputEl.value = "";
  await refresh();
});

refresh().catch((err) => console.error(err));
