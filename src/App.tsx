import { useState, FormEvent, ChangeEvent } from 'react';
import './index.css'; // Make sure to import the CSS file

// Define the form data type
type FormData = {
  date: string;
  time: string;
  amount: number | '';
  note: string;
};

const generateTimeOptions = () => {
  const times = [];
  for (let hour = 0; hour < 24; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      times.push(time);
    }
  }
  return times;
};

const timeOptions = generateTimeOptions();

function App() {
  // State to store the form data with TypeScript type
  const [formData, setFormData] = useState<FormData>({
    date: new Date().toISOString().substr(0, 10), // Default to current date in YYYY-MM-DD format
    time: '',
    amount: '',
    note: ''
  });

  // Function to handle form input changes with TypeScript type
  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: name === 'amount' ? (value ? parseInt(value) : '') : value
    }));
  };

  // Function to handle form submission with TypeScript type
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log(formData);
    // Here you would typically send the data to a backend server or store it in local state or database
  };

  return (
    <div className="App p-4">
      <h1 className="text-2xl font-bold mb-4">Baby Eating Tracker</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2">Date:</label>
          <input
            className="border-2 border-gray-200 rounded p-2 w-full"
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
          />
        </div>
        <div>
          <label className="block mb-2">Time:</label>
          <select
            className="border-2 border-gray-200 rounded p-2 w-full"
            name="time"
            value={formData.time}
            onChange={handleChange}
          >
            <option value="">Select time</option>
            {timeOptions.map((time) => (
              <option key={time} value={time}>
                {time}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block mb-2">Amount (ml):</label>
          <input
            className="border-2 border-gray-200 rounded p-2 w-full"
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
          />
        </div>
        <div>
          <label className="block mb-2">Note:</label>
          <textarea
            className="border-2 border-gray-200 rounded p-2 w-full"
            name="note"
            value={formData.note}
            onChange={handleChange}
          />
        </div>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700 transition duration-300">
          Save Entry
        </button>
      </form>
    </div>
  );
}

export default App;