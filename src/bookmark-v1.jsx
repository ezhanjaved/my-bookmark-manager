import { useEffect, useState } from "react";
import "./App.css";

export default function BookmarkSaverApp() {
    const [response, setResponse] = useState(false);
    const [page, setPage] = useState(false);
    const [mainData, setmainData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            const response = await fetch("http://127.0.0.1:8000/fetch-bookmark", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) {

            }

            const result = await response.json();
            setmainData(result);
            setResponse(false);
        }
        fetchData();
    }, [response])

    return (
        <>
            {!page ? (
                <BookmarkSaver setResponse={setResponse} />
            ) : (
                <BookmarkStorage mainData={mainData} />
            )}
            <div className="switch-btn" onClick={() => setPage(prev => !prev)}>
                <i className="fa-solid fa-x"></i>
            </div>
        </>
    );
}

function BookmarkSaver({ setResponse }) {
    const [url, setURL] = useState("");
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);

    const sendURL = async () => {
        if (!url) return;

        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:8000/save-bookmark", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                throw new Error("An error was encountered");
            }

            const result = await response.json();
            if (result.status === 1) { // check for URL presence too
                setLoading(false);
                setStatus(true);
                setResponse(true);
            } else {
                setLoading(false);
                setStatus(false);
            }
        } catch (error) {
            setLoading(false);
            console.error("Error sending URL:", error);
            setStatus(false);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {status != null && (
                <div className="status-popup">
                    <i className="fa-solid fa-bookmark"></i>
                    <p>{status === true ? "✅ Bookmark added successfully!" : "❌ Sorry, something went wrong."}</p>
                    <button onClick={() => setStatus(null)}>Okay</button>
                </div>
            )}
            {loading && (
                <div className="status-popup">
                    <i className="fa-solid fa-clock"></i>
                    <p>Loading...</p>
                </div>
            )}
            <div id="bookmark-manager">
                <i className="fa-solid fa-bookmark"></i>
                <h1>Bookmark Manager</h1>
                <p>Enter the URL to save it as a bookmark</p>
                <input
                    type="text"
                    value={url}
                    onChange={e => setURL(e.target.value)}
                />
                <button onClick={sendURL}>Submit</button>
            </div>
        </>
    );
}

function BookmarkStorage({ mainData }) {

    const data = mainData?.bookmarks?.[0]?.data;

    return (
        <div id="bookmark-storage">
            <h2>Stored Bookmarks</h2>
            <div id="grid-maintain">
                {data && data.length > 0 ? (
                    data.map((bookmark, index) => (
                        <div className="boxed" key={index}>
                            <div className="image-box">
                                <img src={bookmark.screenshot_url} alt={`Screenshot of ${bookmark.title}`} />
                            </div>
                            <div className="data-box">
                                <img src={bookmark.favicon} alt="Favicon" />
                                <p>Title: {bookmark.title}</p>
                                <p>Description: {bookmark.description}</p>
                                <p>Saved by: {bookmark.generated_by}</p>
                                <div
                                    style={{
                                        display: "flex",
                                        flexDirection: "row",
                                        gap: "20px",
                                        background: "none",
                                        marginTop: "5px"
                                    }}
                                >
                                    <button>
                                        <a href={bookmark.url} target="_blank" rel="noopener noreferrer">Visit Website</a>
                                    </button>
                                    <button>
                                        <a href={bookmark.archive_url} target="_blank" rel="noopener noreferrer">Wayback Machine</a>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <p>No bookmarks saved yet.</p>
                )}
            </div>
        </div>
    );

}