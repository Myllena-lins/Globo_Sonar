import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="flex flex-col gap-24">
            <div className="container mx-auto px-6">
                <h2>Not Found</h2>
                <p>Could not find requested resource</p>
                <Link href="/">Return Home</Link>
            </div>
        </div>
    );
}