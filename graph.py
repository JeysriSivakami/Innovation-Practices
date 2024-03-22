def graph(transactions,portfolio_values):
    plt.plot(transactions, portfolio_values, marker='o')
    # Adding labels and title
    plt.xlabel('Transactions')
    plt.ylabel('Portfolio Value')
    plt.title('Portfolio Performance Over Time')
    
    # Rotating x-axis labels for better readability
    plt.xticks(rotation=45)

    # Displaying the graph
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.show()

#ATTENTION!!!!!!
#INITIALIZE TRANSACTION DATE LIST AND PORTFOLIO_VAL LIST INSIDE STRATEGY(RECORDS,TOKEN) FUNCTION
transac_date=[]
portfolio_val=[]
#ADD THESE 2 LINES AFTER SELL CONDITION
transac_date.append(record['date'].date())
portfolio_val.append(portfolio)
#CALL THE FUNCTION AFTER PRINTING PROFIT
graph(transac_date,portfolio_val)
