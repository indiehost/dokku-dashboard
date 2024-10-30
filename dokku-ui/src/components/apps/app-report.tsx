import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '@/lib/utils';
import Loader from '@/components/shared/loader'

export default function AppReport() {
    const { appName } = useParams();

    const { data: appDetails, isLoading, error } = useQuery({
        queryKey: ['app', appName],
        queryFn: () => apiRequest(`/apps/${appName}`),
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
                    <p><strong>Application name:</strong> {appDetails?.name || appName}</p>
                    <p><strong>Created at:</strong> {new Date(Number(appDetails?.app_created_at) * 1000).toLocaleString()}</p>
                    <p><strong>Deploy source:</strong> {appDetails?.app_deploy_source}</p>
                    <p><strong>Deploy source URL:</strong> {appDetails?.app_deploy_source_metadata}</p>
                    <p><strong>App directory:</strong> {appDetails?.app_dir}</p>
                    <p><strong>Locked:</strong> {appDetails?.app_locked === "true" ? "Yes" : "No"}</p>
                </div>
            </CardContent>
        </Card>
    );
}
