import AppsList from "@/components/apps-list";
import { Button } from "@/components/ui/button";

export default function Home() {

    const handleCreateApp = () => {
        console.log("Create App");
    };

    return (
        <main className="flex-grow p-6 overflow-auto">

            {/* Apps */}
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Apps</h2>
                <Button onClick={handleCreateApp}>
                    Create App
                </Button>
            </div>

            <AppsList />
            

            {/* SSH Keys */}
            <div className="flex justify-between items-center mb-4 mt-8">
                <h2 className="text-2xl font-bold">SSH Keys</h2>
            </div>
        </main>
    )
}
