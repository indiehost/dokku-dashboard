import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

export default function DokkuTerminal() {
    const [command, setCommand] = useState('')
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

    const handleSubmit = () => {
        if (command.trim() && !isPending) {
            const cleanCommand = command.trim().replace(/^dokku\s+/, '') // Remove dokku prefix if present
            mutate(cleanCommand)
        }
    }

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Dokku Terminal</CardTitle>
                <CardDescription>Execute Dokku commands directly via the dokku-daemon</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <div className="flex gap-2 max-w-md">
                        <Input
                            id="command"
                            value={command}
                            onChange={(e) => setCommand(e.target.value)}
                            placeholder="apps:list"
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    handleSubmit()
                                }
                            }}
                        />
                        <Button
                            onClick={handleSubmit}
                            disabled={isPending}
                        >
                            Execute
                        </Button>
                    </div>
                </div>

                <div className="mt-4">
                    <pre className="bg-secondary p-4 rounded-lg overflow-auto min-h-60 max-h-80 whitespace-pre-wrap break-words">
                        {isPending ? (
                            <div className="flex justify-center items-center">
                                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                            </div>
                        ) : output}
                    </pre>
                </div>
            </CardContent>
        </Card>
    )
}
