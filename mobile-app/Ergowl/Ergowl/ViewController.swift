import UIKit

class ViewController: UIViewController {
    
    @IBOutlet weak var lblPosture: UILabel!
    @IBOutlet weak var btnStart: UIButton!
    @IBOutlet weak var btnStop: UIButton!
    @IBOutlet weak var btnSettings: UIButton!
    
    var isUpdatingPosture = false // Flag to control continuous updates
    var timer: Timer?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        btnStop.isHidden = true
    }
    
    @IBAction func btnStop(_ sender: Any) {
        // Stop continuous updates
        btnStart.isHidden = false
        btnStop.isHidden = true
        lblPosture.text = "Start streaming to view data"
        isUpdatingPosture = false
        timer?.invalidate()
    }
    
    @IBAction func btnStart(_ sender: Any) {
        // Hide btnStart and unhide btnStop
        btnStart.isHidden = true
        btnStop.isHidden = false
        
        // Start timer to call getPosture every 10 seconds
        timer = Timer.scheduledTimer(withTimeInterval: 10, repeats: true) { _ in
            print("Timer is firing...")
            self.getPosture { postureInfo in
                DispatchQueue.main.async {
                    self.lblPosture.text = postureInfo
                    print("Posture Info: \(postureInfo)")
                }
            }
        }
        // Call immediately upon starting
        timer?.fire()
    }



    func getPosture(completion: @escaping (String) -> Void) {
        let url = URL(string: "http://172.20.10.2:80/posture")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = "posture".data(using: .utf8)
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                completion("Failed")
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200,
                  let contentType = httpResponse.allHeaderFields["Content-Type"] as? String,
                  contentType == "text/plain", // Assuming the content type is text/plain
                  let data = data,
                  let postureInfo = String(data: data, encoding: .utf8) else {
                print("Unexpected response: \(response.debugDescription)")
                completion("Failed")
                return
            }
            
            completion(postureInfo)
        }
        task.resume()
    }
}
