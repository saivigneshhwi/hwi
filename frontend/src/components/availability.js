import React from "react";

const Availability = () => {
    // Static data for now
    const availabilityData = {
        boats: { left: 5, total: 10 },
        lifeJackets: { left: 25, total: 40 },
    };

    return (
        <div className="availability">
            <h2>Availability</h2>
            <ul>
                <li>
                    🚤 Boats: {availabilityData.boats.left} / {availabilityData.boats.total}
                </li>
                <li>
                    🦺 Life Jackets: {availabilityData.lifeJackets.left} / {availabilityData.lifeJackets.total}
                </li>
            </ul>
        </div>
    );
};

export default Availability;
