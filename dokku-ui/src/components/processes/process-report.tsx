import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '@/lib/utils';
import Loader from '@/components/shared/loader'

export default function ProcessReport() {
    const { appName } = useParams();

    const { data: appDetails, isLoading, error } = useQuery({
        queryKey: ['app', appName, 'status'],
        queryFn: () => apiRequest(`/apps/${appName}/status`),
    });


    if (isLoading) return <Loader />
    if (error) return <div>An error occurred: {error.message}</div>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>{appDetails?.name || appName}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-2">
                    <p><strong>Status:</strong> {appDetails?.running === "true" ? "Running" : "Stopped"}</p>
                    <p><strong>Deployed:</strong> {appDetails?.deployed === "true" ? "Yes" : "No"}</p>
                    <p><strong>Process Count:</strong> {appDetails?.processes}</p>
                    <p><strong>Can Scale:</strong> {appDetails?.ps_can_scale === "true" ? "Yes" : "No"}</p>
                    <p><strong>Restart Policy:</strong> {appDetails?.ps_restart_policy}</p>
                    <p><strong>Procfile Path:</strong> {appDetails?.ps_computed_procfile_path}</p>
                    {appDetails?.status_web_1 && (
                        <p><strong>Web Process Status:</strong> {appDetails.status_web_1}</p>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
