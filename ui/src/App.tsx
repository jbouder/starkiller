import { ThemeProvider } from "@/components/theme-provider";
import { ErrorBoundary } from "@/components/error-boundary";
import { Header } from "@/components/layout/header";
import { MainContent } from "@/components/layout/main-content";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="starkiller-theme">
      <ErrorBoundary>
        <div className="min-h-screen bg-background text-foreground">
          <Header />
          <MainContent />
        </div>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
