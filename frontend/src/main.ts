import { createApi, type Todo } from "./api";

const API_URL = import.meta.env.VITE_API_URL;
if (!API_URL) {
  throw new Error("VITE_API_URL is not set. Copy .env.example to .env at the repo root.");
}

const api = createApi(API_URL);

const listEl = document.getElementById("todo-list") as HTMLUListElement;
const formEl = document.getElementById("new-todo-form") as HTMLFormElement;
const inputEl = document.getElementById("new-todo-input") as HTMLInputElement;

function render(todos: Todo[]): void {
  listEl.innerHTML = "";
  for (const todo of todos) {
    const li = document.createElement("li");
    if (todo.done) li.classList.add("done");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.done;
    checkbox.addEventListener("change", async () => {
      await api.updateTodo({ ...todo, done: checkbox.checked });
      await refresh();
    });

    const title = document.createElement("span");
    title.textContent = todo.title;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Delete";
    removeBtn.addEventListener("click", async () => {
      await api.deleteTodo(todo.id);
      await refresh();
    });

    li.append(checkbox, title, removeBtn);
    listEl.appendChild(li);
  }
}

async function refresh(): Promise<void> {
  const todos = await api.fetchTodos();
  render(todos);
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = inputEl.value.trim();
  if (!title) return;
  await api.createTodo(title);
  inputEl.value = "";
  await refresh();
});

refresh().catch((err) => console.error(err));
