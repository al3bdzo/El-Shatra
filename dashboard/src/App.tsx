// Routes. A new page = a component in src/pages/ plus one <Route> here.
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Home } from "./pages/Home";
import { LiveGame } from "./pages/LiveGame";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/games/:id" element={<LiveGame />} />
      </Routes>
    </BrowserRouter>
  );
}
