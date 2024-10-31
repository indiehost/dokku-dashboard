import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, RefreshCw } from "lucide-react"

export default function AppLogs({ appName }: { appName: string | undefined }) {
    const { data, isLoading, refetch } = useQuery({
        queryKey: ['logs', appName],
        queryFn: () => apiRequest(`/logs/${appName}`),
        enabled: !!appName,
    })

    const handleRefresh = () => {
        if (!isLoading && appName) {
            refetch()
        }
    }

    return (
        <Card className="w-full">
            <CardHeader className="flex flex-row items-center justify-between">
                <div>
                    <CardTitle>{appName} logs</CardTitle>
                    <CardDescription>Showing the last 100 lines of the {appName} logs</CardDescription>
                </div>
                <Button
                    variant="outline"
                    size="icon"
                    onClick={handleRefresh}
                    disabled={isLoading}
                >
                    <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                </Button>
            </CardHeader>
            <CardContent>
                <pre className="bg-secondary p-4 rounded-lg overflow-auto h-72 whitespace-pre-wrap break-words">
                    {isLoading ? (
                        <div className="flex justify-center items-center">
                            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                    ) : data}
                </pre>
            </CardContent>
        </Card>
    )
}
