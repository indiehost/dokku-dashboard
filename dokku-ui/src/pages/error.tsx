import { Link } from 'react-router-dom';
export default function Error() {
    return (
      <div className="flex flex-col items-center justify-center h-screen space-y-4">
        <h1 className="text-4xl font-bold">Oops! Something went wrong</h1>
        <Link to="/">Go home</Link>
      </div>
    );
}
