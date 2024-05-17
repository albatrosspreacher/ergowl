import Foundation
import UIKit

class SettingsViewController: UIViewController {
    
    @IBOutlet weak var btnConnect: UIButton!
    @IBOutlet weak var btnDisconnect: UIButton!
    @IBOutlet weak var btnStatus: UILabel!
    @IBOutlet weak var btnConfigure: UIButton!
    @IBOutlet weak var lblConfigure: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        btnDisconnect.isHidden = true
        btnStatus.text = "Not connected"
        btnStatus.textAlignment = .center
    }
    
    @IBAction func btnConnect(_ sender: Any) {
        btnConnect.isHidden = true
        btnDisconnect.isHidden = false
        btnStatus.text = "Connecting..."
        btnStatus.textAlignment = .center
        
        let url = URL(string: "http://172.20.10.2:80/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = "connect".data(using: .utf8)
        print(request)
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                DispatchQueue.main.async {
                    self.btnStatus.text = "Connection Failed"
                }
            } else if let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 {
                if let data = data, let message = String(data: data, encoding: .utf8) {
                    print("Response from server: \(message)")
                    DispatchQueue.main.async {
                        self.btnStatus.text = message
                    }
                } else {
                    print("No data received from the server")
                    DispatchQueue.main.async {
                        self.btnStatus.text = "Connected"
                    }
                }
            } else {
                print("Unexpected response: \(response.debugDescription)")
                DispatchQueue.main.async {
                    self.btnStatus.text = "Connection Failed"
                }
            }
        }
        task.resume()
    }


    
    @IBAction func btnDisconnect(_ sender: Any) {
        btnConnect.isHidden = false
        btnDisconnect.isHidden = true
        btnStatus.text = "Not connected"
    }
    
    @IBAction func btnConfigure(_ sender: Any) {
        lblConfigure.text = "Configuring..."
        lblConfigure.textAlignment = .center
        
        let url = URL(string: "http://172.20.10.2:80/configure")!
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = "configure".data(using: .utf8)
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                // Handle error if necessary
            } else if let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 {
                print("Configuration request successful")
                DispatchQueue.main.async {
                    self.lblConfigure.text = "Configuration Complete"
                }
            } else {
                print("Unexpected response: \(response.debugDescription)")
                DispatchQueue.main.async {
                    self.lblConfigure.text = "Configuration Failed"
                }
            }
        }
        task.resume()
    }

}
