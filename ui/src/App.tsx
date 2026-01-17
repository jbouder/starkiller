import { ThemeProvider } from "@/components/theme-provider"

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="starkiller-theme">
      <div className="min-h-screen bg-background text-foreground">
        <div className="container mx-auto py-8">
          <h1 className="text-4xl font-bold mb-4">Starkiller</h1>
          <p className="text-muted-foreground">
            React + TypeScript + Vite + shadcn/ui + Recharts
          </p>
        </div>
      </div>
    </ThemeProvider>
  )
}

export default App
