import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          400: "#5b8def",
          500: "#3366ff",
          600: "#254edb",
          700: "#1c3aa8",
          900: "#111e4d",
        },
      },
    },
  },
  plugins: [],
};

export default config;
