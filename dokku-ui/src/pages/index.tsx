import { Button } from "@/components/ui/button";

export default function Home() {

    const handleCreateApp = () => {
        console.log("Create App");
    };

    return (
        <div className="flex flex-col min-h-screen container mx-auto py-6">
            <main className="flex-grow p-6 overflow-auto">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold">Apps</h2>
                    <Button onClick={handleCreateApp}>
                        Create App
                    </Button>
                </div>
            </main>
        </div>
    )
}
