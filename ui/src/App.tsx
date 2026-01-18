import { ThemeProvider } from "@/components/theme-provider";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Header } from "@/components/layout/Header";
import { MainContent } from "@/components/layout/MainContent";

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
