import AppsList from "@/components/apps/apps-list";
import DokkuTerminal from "@/components/dokku-terminal";
import CreateApp from "@/components/apps/create-app";
import DokkuDaemonLogs from "@/components/logs/dokku-daemon-logs";

export default function Home() {

    return (
        <>
            {/* Apps */}
            <section>
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold">Apps</h2>
                    <CreateApp />
                </div>
                <AppsList />
            </section>

            {/* Sources */}
            {/* <section>
                <div className="flex justify-between items-center mb-4 mt-8">
                    <h2 className="text-2xl font-bold">Sources</h2>
                </div>
                <p>Coming soon</p>
            </section> */}

            {/* Dokku Terminal */}
            <section>
                <DokkuTerminal />
            </section>

            {/* Dokku Daemon Logs */}
            <section>
                <DokkuDaemonLogs />
            </section>
        </>
    )
}
