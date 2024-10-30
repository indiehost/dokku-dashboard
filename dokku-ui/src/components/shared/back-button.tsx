
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function BackButton() {
    const navigate = useNavigate();

    return (
        <div className="flex justify-between items-center">
            <Button variant="outline" onClick={() => navigate('/')}>
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </Button>
        </div>
    )
}