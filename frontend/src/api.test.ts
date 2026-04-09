import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createApi, type Todo } from "./api";

const BASE = "http://api.test";

describe("createApi", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("throws when baseUrl is empty", () => {
    expect(() => createApi("")).toThrowError("API base URL is required");
  });

  it("fetchTodos returns parsed list", async () => {
    const todos: Todo[] = [{ id: 1, title: "a", done: false }];
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => todos,
    });
    const api = createApi(BASE);
    await expect(api.fetchTodos()).resolves.toEqual(todos);
    expect(fetch).toHaveBeenCalledWith(`${BASE}/todos`);
  });

  it("fetchTodos throws on non-ok response", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({ ok: false });
    const api = createApi(BASE);
    await expect(api.fetchTodos()).rejects.toThrow("Failed to fetch todos");
  });

  it("createTodo POSTs title and returns created todo", async () => {
    const created: Todo = { id: 2, title: "buy milk", done: false };
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => created,
    });
    const api = createApi(BASE);
    await expect(api.createTodo("buy milk")).resolves.toEqual(created);
    expect(fetch).toHaveBeenCalledWith(
      `${BASE}/todos`,
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "buy milk", done: false }),
      }),
    );
  });

  it("createTodo throws on failure", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({ ok: false });
    const api = createApi(BASE);
    await expect(api.createTodo("x")).rejects.toThrow("Failed to create todo");
  });

  it("updateTodo PUTs new values", async () => {
    const updated: Todo = { id: 3, title: "new", done: true };
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => updated,
    });
    const api = createApi(BASE);
    await expect(api.updateTodo(updated)).resolves.toEqual(updated);
    expect(fetch).toHaveBeenCalledWith(
      `${BASE}/todos/3`,
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({ title: "new", done: true }),
      }),
    );
  });

  it("updateTodo throws on failure", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({ ok: false });
    const api = createApi(BASE);
    await expect(
      api.updateTodo({ id: 1, title: "x", done: false }),
    ).rejects.toThrow("Failed to update todo");
  });

  it("deleteTodo DELETEs by id", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({ ok: true });
    const api = createApi(BASE);
    await expect(api.deleteTodo(7)).resolves.toBeUndefined();
    expect(fetch).toHaveBeenCalledWith(`${BASE}/todos/7`, { method: "DELETE" });
  });

  it("deleteTodo throws on failure", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({ ok: false });
    const api = createApi(BASE);
    await expect(api.deleteTodo(1)).rejects.toThrow("Failed to delete todo");
  });
});
