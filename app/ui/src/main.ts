import { mount } from "svelte";
import App from "./App.svelte";
import "./app.css";

const target = document.getElementById("app");
if (!target) throw new Error("No se encontró el contenedor de la UI");
mount(App, { target });
