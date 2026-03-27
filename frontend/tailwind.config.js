/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#070b14",
          900: "#0a1020",
          850: "#0d1527",
          800: "#101a31",
        },
        accent: {
          blue: "#38bdf8",
          cyan: "#22d3ee",
          purple: "#8b5cf6",
          green: "#34d399",
          amber: "#fb923c",
          red: "#f87171",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(94,234,212,.14), 0 24px 80px rgba(8,145,178,.18)",
        glass: "0 24px 80px rgba(0,0,0,.34)",
      },
      backgroundImage: {
        "grid-dark":
          "linear-gradient(rgba(148,163,184,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.07) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
