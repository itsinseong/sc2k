// 이미지 파일들을 macOS Vision으로 읽어 글상자를 탭 구분으로 낸다. parse_paxos.py가 호출한다.
// 사용: swift scripts/ocr_vision.swift a.png b.png ...
// 출력: 이미지마다 '#<TAB><경로>' 한 줄, 이어서 '위쪽y<TAB>왼쪽x<TAB>글' (y는 0=맨 위, 1=맨 아래)
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path) else { continue }
    var rect = CGRect(x: 0, y: 0, width: img.size.width, height: img.size.height)
    guard let cg = img.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { continue }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false  // 금액과 날짜를 사전으로 고치지 않게 한다
    try VNImageRequestHandler(cgImage: cg).perform([req])
    print("#\t\(path)")
    for o in req.results ?? [] {
        let b = o.boundingBox
        print(String(format: "%.4f\t%.4f\t%@", 1 - b.maxY, b.minX, o.topCandidates(1)[0].string))
    }
}
