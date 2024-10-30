import { AppActionDialog } from '@/components/apps/app-action-dialog';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '@/lib/utils';
import { toast } from "sonner";

export default function AppActions({ appName }: { appName: string | undefined }) {

    const navigate = useNavigate();
    const [showDeleteDialog, setShowDeleteDialog] = useState(false);
    const [showRestartDialog, setShowRestartDialog] = useState(false);
    const [showStopDialog, setShowStopDialog] = useState(false);
    const [showRebuildDialog, setShowRebuildDialog] = useState(false);

    const { mutate: handleDelete, isPending: isDeleting } = useMutation({
        mutationFn: () => apiRequest(`/apps/${appName}`, { method: 'DELETE' }),
        onSuccess: () => {
            toast.success(`App ${appName} deletion triggered`);
            navigate('/');
        },
        onError: (error) => {
            toast.error(error.message);
        }
    });

    const { mutate: handleRestart, isPending: isRestarting } = useMutation({
        mutationFn: () => apiRequest(`/apps/${appName}/restart`, { method: 'POST' }),
        onSuccess: () => {
            toast.success(`App ${appName} restart triggered`);
            setShowRestartDialog(false);
        },
        onError: (error) => {
            toast.error(error.message);
        }
    });

    const { mutate: handleStop, isPending: isStopping } = useMutation({
        mutationFn: () => apiRequest(`/apps/${appName}/stop`, { method: 'POST' }),
        onSuccess: () => {
            toast.success(`App ${appName} stop triggered`);
            setShowStopDialog(false);
        },
        onError: (error) => {
            toast.error(error.message);
        }
    });

    const { mutate: handleRebuild, isPending: isRebuilding } = useMutation({
        mutationFn: () => apiRequest(`/apps/${appName}/rebuild`, { method: 'POST' }),
        onSuccess: () => {
            toast.success(`App ${appName} rebuild triggered`);
            setShowRebuildDialog(false);
        },
        onError: (error) => {
            toast.error(error.message);
        }
    });

    return (<>
        <div className="flex gap-2">
            <Button
                variant="outline"
                onClick={() => setShowRestartDialog(true)}
            >
                Restart app
            </Button>
            <Button
                variant="outline"
                onClick={() => setShowStopDialog(true)}
            >
                Stop app
            </Button>
            <Button
                variant="outline"
                onClick={() => setShowRebuildDialog(true)}
            >
                Rebuild app
            </Button>
            <Button
                variant="destructive"
                onClick={() => setShowDeleteDialog(true)}
            >
                Delete app
            </Button>
        </div>

        <AppActionDialog
            isOpen={showDeleteDialog}
            onOpenChange={setShowDeleteDialog}
            onConfirm={() => handleDelete()}
            title="Delete App"
            description={`Are you sure you want to delete ${appName}? This action cannot be undone. Will execute "dokku apps:destroy ${appName}"`}
            actionLabel="Delete"
            isLoading={isDeleting}
        />

        <AppActionDialog
            isOpen={showRestartDialog}
            onOpenChange={setShowRestartDialog}
            onConfirm={() => handleRestart()}
            title="Restart App"
            description={`Are you sure you want to restart ${appName}?`}
            actionLabel="Restart"
            isLoading={isRestarting}
        />

        <AppActionDialog
            isOpen={showStopDialog}
            onOpenChange={setShowStopDialog}
            onConfirm={() => handleStop()}
            title="Stop App"
            description={`Are you sure you want to stop ${appName}?`}
            actionLabel="Stop"
            isLoading={isStopping}
        />

        <AppActionDialog
            isOpen={showRebuildDialog}
            onOpenChange={setShowRebuildDialog}
            onConfirm={() => handleRebuild()}
            title="Rebuild App"
            description={`Are you sure you want to rebuild ${appName}?`}
            actionLabel="Rebuild"
            isLoading={isRebuilding}
        />
    </>)
}