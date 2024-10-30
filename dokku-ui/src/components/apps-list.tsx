
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function AppsList() {

    const { data: apps, isLoading, error } = useQuery<string[]>({
        queryKey: ['apps'],
        queryFn: () => apiRequest(`/apps`),
    })


    if (isLoading) return <div>Loading...</div>
    if (error) return <div>An error occurred: {error.message}</div>

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {apps?.map(applicationName => (
                <Card
                    key={applicationName}
                    className="cursor-pointer hover:shadow-lg transition-shadow"
                >
                    <CardHeader>
                        <CardTitle>{applicationName}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p><strong>Application name:</strong> {applicationName}</p>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}
