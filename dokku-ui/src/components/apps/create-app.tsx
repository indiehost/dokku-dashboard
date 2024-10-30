import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/utils";
import { toast } from "sonner"
import { Loader2 } from "lucide-react";

export default function CreateApp() {
    const [open, setOpen] = useState(false);
    const [appName, setAppName] = useState("");
    const queryClient = useQueryClient();

    const createAppMutation = useMutation({
        mutationFn: (name: string) => apiRequest("/apps", {
            method: "POST",
            body: JSON.stringify({ name }),
        }),
        onSuccess: () => {
            toast.success("App created successfully");
            setOpen(false);
            setAppName("");
            queryClient.invalidateQueries({ queryKey: ["apps"] });
        },
        onError: (error) => {
            toast.error(error.message);
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        createAppMutation.mutate(appName);
    };

    return (
        <>
            <Button onClick={() => setOpen(true)}>Create App</Button>
            
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Create New App</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleSubmit}>
                        <div className="py-4">
                            <Input
                                placeholder="Enter app name"
                                value={appName}
                                onChange={(e) => setAppName(e.target.value)}
                                disabled={createAppMutation.isPending}
                            />
                        </div>
                        <DialogFooter>
                            <Button
                                type="submit"
                                disabled={!appName || createAppMutation.isPending}
                            >
                                {createAppMutation.isPending && (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                )}
                                Create
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </>
    );
}
