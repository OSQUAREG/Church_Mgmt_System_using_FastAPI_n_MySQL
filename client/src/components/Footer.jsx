import React from 'react';

const Footer = () => {
    const currentYear = new Date().getFullYear();
    return (
        <>
            <br /><br /><br /><br /><br />
            <div class="text-md-center text-muted bg-dark fixed-bottom footer">
                <footer style={{ textAlign: 'center' }}>
                    <p class="text-light">
                        <small>
                            &copy; Gregory (OSQUAREG Tech World) {currentYear}{" "}
                            | ChurchMan - Church Management Solutions
                        </small>
                    </p>
                </footer>
            </div>
        </>
    )
};

export default Footer;