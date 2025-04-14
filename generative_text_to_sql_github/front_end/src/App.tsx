import React, { useState } from 'react';

interface TableData {
  columns: string[];
  rows: any[][];
}

interface Message {
  text: string;
  sender: 'user' | 'ai';
  tableData?: TableData;
}

function ChatApp() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  // Function to handle user input submission
  const handleQuerySubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    const userMessage: Message = { text: query, sender: 'user' };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    
    // Clear input field
    setQuery('');

    // Call backend to get SQL from LLM and execute it
    try {
      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: query }),
      });

      console.log('Raw Response:', response);
      const data = await response.json();
      console.log('Parsed Data:', data);
      
      // Convert the results into table format
      let tableData: TableData | undefined;
      if (Array.isArray(data) && data.length > 0) {
        console.log('First Result:', data[0]);
        // Get all columns from the first result, excluding CREATED_AT and UPDATED_AT
        const columns = Object.keys(data[0]).filter(col => 
          col !== 'CREATED_AT' && col !== 'UPDATED_AT'
        );
        console.log('Columns:', columns);
        // Convert each result object to an array of values in the same order as columns
        const rows = data.map((row: Record<string, any>) => {
          console.log('Processing row:', row);
          return columns.map(col => row[col]);
        });
        tableData = { columns, rows };
        console.log('Final Table Data:', tableData);
      }

      const aiMessage: Message = { 
        text: `Here is the result. ${data.length} row(s) are returned:`,
        sender: 'ai',
        tableData
      };
      setMessages([...newMessages, aiMessage]);
    } catch (error) {
      const errorMessage: Message = { text: "Error processing the request.", sender: 'ai' };
      setMessages([...newMessages, errorMessage]);
    }
  };

  return (
    <div className="chat-container" style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <h1 style={{
        textAlign: 'center',
        color: '#333',
        marginBottom: '30px',
        fontSize: '28px',
        fontWeight: 'bold'
      }}>SQL Query Assistant</h1>
      
      <div className="messages" style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        flex: 1,
        overflowY: 'auto',
        marginBottom: '20px'
      }}>
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`} style={{
            backgroundColor: msg.sender === 'user' ? '#e3f2fd' : '#f1f1f1',
            padding: '15px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            maxWidth: '90%',
            marginLeft: msg.sender === 'user' ? 'auto' : '0',
            marginRight: msg.sender === 'user' ? '0' : 'auto'
          }}>
            <p style={{
              margin: '0 0 10px 0',
              fontSize: '16px',
              color: '#333'
            }}><strong style={{
              color: msg.sender === 'user' ? '#1976d2' : '#4CAF50'
            }}>{msg.sender.toUpperCase()}:</strong> {msg.text}</p>
            {msg.tableData && (
              <div className="table-container" style={{ 
                marginTop: '10px', 
                overflowX: 'auto',
                width: '100%',
                borderRadius: '4px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                <table style={{ 
                  borderCollapse: 'collapse', 
                  width: '100%',
                  fontSize: '12px'
                }}>
                  <thead>
                    <tr>
                      {msg.tableData.columns.map((col, i) => (
                        <th key={i} style={{ 
                          border: '1px solid #ddd', 
                          padding: '12px', 
                          textAlign: 'left',
                          backgroundColor: '#4CAF50',
                          color: 'white',
                          position: 'sticky',
                          top: 0,
                          fontWeight: 'bold'
                        }}>
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {msg.tableData.rows.map((row, i) => (
                      <tr key={i} style={{ 
                        backgroundColor: i % 2 === 0 ? '#ffffff' : '#f9f9f9',
                        transition: 'background-color 0.2s',
                        cursor: 'pointer'
                      }} onMouseOver={(e) => {
                        e.currentTarget.style.backgroundColor = '#f0f0f0';
                      }} onMouseOut={(e) => {
                        e.currentTarget.style.backgroundColor = i % 2 === 0 ? '#ffffff' : '#f9f9f9';
                      }}>
                        {row.map((cell, j) => (
                          <td key={j} style={{ 
                            border: '1px solid #ddd', 
                            padding: '10px',
                            textAlign: typeof cell === 'number' ? 'right' : 'left'
                          }}>
                            {typeof cell === 'number' ? cell.toLocaleString() : cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleQuerySubmit} style={{
        display: 'flex',
        gap: '10px',
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.1)',
        position: 'sticky',
        bottom: '20px'
      }}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your query..."
          style={{ 
            flex: 1,
            padding: "12px", 
            borderRadius: "4px",
            border: "1px solid #ddd",
            fontSize: "16px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            minHeight: "60px",
            maxHeight: "200px",
            resize: "vertical",
            fontFamily: "inherit"
          }}
        />
        <button type="submit" style={{
          padding: "8px 16px",
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          fontSize: "14px",
          fontWeight: "bold",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          transition: "background-color 0.3s",
          alignSelf: "flex-end",
          marginBottom: "8px"
        }}>Submit</button>
      </form>
    </div>
  );
}

export default ChatApp;
