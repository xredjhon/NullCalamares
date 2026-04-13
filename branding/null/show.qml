import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation

    function onActivate() {
        slideTimer.start()
    }

    function onLeave() {
        slideTimer.stop()
    }

    property int currentSlide: 0

    Rectangle {
        anchors.fill: parent
        color: "#050607"
    }

    Image {
        id: background
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        source: currentSlide === 0 ? "assets/slide-system.png" : currentSlide === 1 ? "assets/slide-dev.png" : "assets/slide-privacy.png"
        opacity: 0.34
    }

    Rectangle {
        anchors.fill: parent
        color: "#050607"
        opacity: 0.58
    }

    Image {
        id: logo
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.10
        source: "assets/logo.png"
        sourceSize.width: 220
        fillMode: Image.PreserveAspectFit
    }

    Column {
        width: parent.width * 0.62
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 18

        Text {
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            text: currentSlide === 0 ? "Controlled and modular installation for NullLinux" : currentSlide === 1 ? "Prepare the development environment during installation" : "Add privacy and defensive tools from curated profiles"
            color: "#F4FFF8"
            wrapMode: Text.WordWrap
            font.pixelSize: 34
            font.bold: true
        }

        Text {
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            text: currentSlide === 0 ? "Branding, streamlined flow, and profile-based package selection are built into NullCalamares." : currentSlide === 1 ? "Compilers, containers, virtualization, and workstation tools are managed as clean installation profiles." : "Only packages that can be handled safely during installation are installed directly from the repository layer."
            color: "#C7D8CD"
            wrapMode: Text.WordWrap
            font.pixelSize: 20
        }
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 48
        spacing: 10

        Repeater {
            model: 3

            Rectangle {
                width: index === currentSlide ? 34 : 12
                height: 12
                radius: 6
                color: index === currentSlide ? "#52FF8F" : "#335743"

                Behavior on width {
                    NumberAnimation { duration: 180 }
                }
            }
        }
    }

    Timer {
        id: slideTimer
        interval: 4000
        repeat: true
        running: true
        onTriggered: presentation.currentSlide = (presentation.currentSlide + 1) % 3
    }
}
