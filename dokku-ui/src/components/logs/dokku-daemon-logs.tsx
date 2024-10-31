import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, RefreshCw } from "lucide-react"

export default function DokkuDaemonLogs() {
    const [output, setOutput] = useState<string | null>(null)

    const { mutate, isPending } = useMutation({
        mutationFn: (cmd: string) => apiRequest('/dokku/command', {
            method: 'POST',
            body: JSON.stringify({ command: cmd }),
        }),
        onSuccess: (data) => {
            setOutput(JSON.stringify(data, null, 2))
        },
    })

    const handleRefresh = () => {
        if (!isPending) {
            mutate('logs dokku-daemon')
        }
    }

    return (
        <Card className="w-full">
            <CardHeader className="flex flex-row items-center justify-between">
                <div>
                    <CardTitle>Dokku Daemon Logs</CardTitle>
                    <CardDescription>Showing the last 100 lines of the dokku-daemon logs</CardDescription>
                </div>
                <Button
                    variant="outline"
                    size="icon"
                    onClick={handleRefresh}
                    disabled={isPending}
                >
                    <RefreshCw className={`h-4 w-4 ${isPending ? 'animate-spin' : ''}`} />
                </Button>
            </CardHeader>
            <CardContent>
                <pre className="bg-secondary p-4 rounded-lg overflow-auto min-h-60 max-h-80 whitespace-pre-wrap break-words">
                    {isPending ? (
                        <div className="flex justify-center items-center">
                            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                    ) : output}
                </pre>
            </CardContent>
        </Card>
    )
}
