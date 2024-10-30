import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useNavigate } from 'react-router-dom'
import Loader from '@/components/shared/loader'

export default function AppsList() {
    const navigate = useNavigate()

    const { data: apps, isLoading, error } = useQuery<string[]>({
        queryKey: ['apps'],
        queryFn: () => apiRequest(`/apps`),
    })

    if (isLoading) return <Loader />
    if (error) return <div>An error occurred: {error.message}</div>

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {apps?.map(applicationName => (
                <Card
                    key={applicationName}
                    className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.01]"
                    onClick={() => navigate(`/apps/${applicationName}`)}
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
