import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '@/lib/utils';
import Loader from '@/components/shared/loader'

export default function DomainReport() {
    const { appName } = useParams();

    const { data: appDetails, isLoading, error } = useQuery({
        queryKey: ['app', appName, 'domains'],
        queryFn: () => apiRequest(`/apps/${appName}/domains`),
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
                    <p><strong>App Domains Enabled:</strong> {appDetails?.domains_app_enabled === "true" ? "Yes" : "No"}</p>
                    <p><strong>App Virtual Hosts:</strong> {appDetails?.domains_app_vhosts?.split(' ').map((host: string) => (
                        <a href={`https://${host}`} target="_blank" key={host} className="ml-2 underline">{host}</a>
                    ))}</p>
                    <p><strong>Global Domains Enabled:</strong> {appDetails?.domains_global_enabled === "true" ? "Yes" : "No"}</p>
                    <p><strong>Global Virtual Hosts:</strong> {appDetails?.domains_global_vhosts?.split(' ').map((host: string) => (
                        <a href={`https://${host}`} target="_blank" key={host} className="ml-2 underline">{host}</a>
                    ))}</p>
                </div>
            </CardContent>
        </Card>
    );
}
