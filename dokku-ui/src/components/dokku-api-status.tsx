import { apiRequest } from "@/lib/utils";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function ApiStatus() {
    const [showUpdateDialog, setShowUpdateDialog] = useState(false);
    const queryClient = useQueryClient();

    // Fetch api status from /health endpoint
    const { data: health, isLoading, error } = useQuery({
        queryKey: ['health'],
        queryFn: () => apiRequest('/health')
    });

    // Trigger deployment of latest dokku-api from git
    const { mutate: handleUpdate } = useMutation({
        mutationFn: () => apiRequest('/update', { method: 'POST' }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['health'] });
            setShowUpdateDialog(false);
        }
    });

    if (isLoading) {
        return <p className="text-center mb-4">Loading...</p>;
    }

    if (error) {
        return <p className="text-center mb-4">Error: Unable to fetch API status</p>;
    }

    return (
        <>
            {health && (
                <p className="text-center">
                    Status: {health.status} | Database: {health.database} | Dokku: {health.dokku} | Version: {health.version}&nbsp;

                    {/* Update button with confirmation dialog */}
                    <AlertDialog open={showUpdateDialog} onOpenChange={setShowUpdateDialog}>
                        <Button variant="link" className="underline p-0 h-auto" onClick={() => setShowUpdateDialog(true)}>
                            (update)
                        </Button>
                        <AlertDialogContent>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Confirm Update</AlertDialogTitle>
                                <AlertDialogDescription>
                                    This will clone and deploy the latest of 'dokku-api' from the git repo <a className="underline" href="https://github.com/indiehost/dokku-dashboard" target="_blank">https://github.com/indiehost/dokku-dashboard</a> using <code>dokku git:sync</code>
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={() => handleUpdate()}>
                                    Update
                                </AlertDialogAction>
                            </AlertDialogFooter>
                        </AlertDialogContent>
                    </AlertDialog>
                </p>
            )}
        </>
    )
}
