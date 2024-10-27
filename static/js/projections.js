function loadSalesProjection() {
    const employeeId = document.getElementById('employee-dropdown').value;
    const month = document.getElementById('month').value;
    const year = document.getElementById('year').value;

    if (!employeeId) {
        return;
    }

    // Show loading modal
    $('#loadingModal').modal('show');

    $.ajax({
        url: '/metrics/get_sales_projection',
        type: 'GET',
        data: {
            sales_agent_id: employeeId,
            month: month,
            year: year
        },
        success: function(response) {
            // Hide loading modal
            $('#loadingModal').modal('hide');

            // Populate form fields with the received data
            if (response.projection) {
                document.getElementById('leadCount').value = response.projection.total_call_slots;
                document.getElementById('closeRate').value = response.projection.closure_percentage_projected;
                document.getElementById('appointment_booked_projection').value = response.projection.appointment_booked_projection;
                document.getElementById('show_up_rate_projection').value = response.projection.show_up_rate_projection;
                document.getElementById('costPerLead').value = response.projection.cost_per_lead;
                document.getElementById('averageSaleValue').value = response.projection.sale_price;
                
                // Update goal fields
                document.getElementById('appointment_booked_goal').value = response.projection.appointment_booked_goal;
                document.getElementById('show_up_rate_goal').value = response.projection.show_up_rate_goal;
                
                // Trigger calculation
                calculateMetrics();
            } else {
                // Clear form fields if no projection data is found
                document.getElementById('leadCount').value = '';
                document.getElementById('closeRate').value = '';
                document.getElementById('appointment_booked_projection').value = '';
                document.getElementById('show_up_rate_projection').value = '';
                document.getElementById('costPerLead').value = '';
                document.getElementById('averageSaleValue').value = '';
                document.getElementById('appointment_booked_goal').value = '';
                document.getElementById('show_up_rate_goal').value = '';
            }
        },
        error: function(xhr, status, error) {
            // Hide loading modal
            $('#loadingModal').modal('hide');
            
            console.error('Error fetching sales projection:', error);
            alert('An error occurred while fetching the sales projection. Please try again.');
        }
    });
}

function formatIndianRupee(number) {
    return new Intl.NumberFormat('en-IN').format(number);
}

function calculateMetrics() {
    const totalCallSlots = parseInt($('#sales_slots_possible').val());
    
    // Calculate goal values
    const bookingRateGoal = parseFloat($('#appointment_booked_goal').val());
    const showUpRateGoal = parseFloat($('#show_up_rate_goal').val()) / 100;
    const closeRateGoal = parseFloat($('#close_rate_goal').val()) / 100;
    const leadGenerationGoal = Math.round((totalCallSlots *100) / bookingRateGoal);
    const appointmentCountGoal = Math.round(leadGenerationGoal * (bookingRateGoal / 100));
    const attendedCountGoal = Math.round(appointmentCountGoal * showUpRateGoal);
    const salesCountGoal = Math.round(attendedCountGoal * closeRateGoal);

    $('#appointment_booked_goal_value').text(appointmentCountGoal);
    $('#show_up_rate_goal_value').text(attendedCountGoal);
    $('#sales_goal_closure_rate_value').text(salesCountGoal);
    // Update the lead generation goal input field
    $('#lead_generation_goal').val(leadGenerationGoal);

    // Calculate goal values
    const bookingRateProjection = parseFloat($('#appointment_booked_projection').val());
    const showUpRateProjection = parseFloat($('#show_up_rate_projection').val()) / 100;
    const closeRateProjection = parseFloat($('#close_rate_projection').val()) / 100;
    const leadGenerationProjection = Math.round((totalCallSlots *100) / bookingRateProjection);
    const appointmentCountProjection = Math.round(leadGenerationProjection * (bookingRateProjection / 100));
    const attendedCountProjection = Math.round(appointmentCountProjection * showUpRateProjection);
    const salesCountProjection = Math.round(attendedCountProjection * closeRateProjection);

    $('#appointment_booked_projection_value').text(appointmentCountProjection);
    $('#show_up_rate_projection_value').text(attendedCountProjection);
    $('#sales_projected_closure_rate_value').text(salesCountProjection);
    // Update the lead generation goal input field
    $('#lead_generation_projection').val(leadGenerationProjection);
    const costPerLead = parseFloat($('#costPerLead').val());
    const averageSaleValue = parseFloat($('#averageSaleValue').val());
    
    const totalLeadCost = leadGenerationGoal * costPerLead;
    const appointmentCost = totalLeadCost / appointmentCountProjection;
    const attendedCost = totalLeadCost / attendedCountProjection;
    const saleCost = totalLeadCost / salesCountProjection;

    $('#projected_lead_cost').text(formatIndianRupee(totalLeadCost.toFixed(2)));
    $('#lead_cost').text(formatIndianRupee(totalLeadCost.toFixed(2)));
    $('#appointment_booked_cost').text(formatIndianRupee(appointmentCost.toFixed(2)));
    $('#show_up_rate_cost').text(formatIndianRupee(attendedCost.toFixed(2)));
    $('#sales_projected_closure_cost').text(formatIndianRupee(saleCost.toFixed(2)));

    const totalRevenue = salesCountProjection * averageSaleValue;
    const totalCost = totalLeadCost;
    const netProfit = totalRevenue - totalCost;
    const roi = totalRevenue / totalCost;

    $('#totalProjectedRevenue').text(formatIndianRupee(totalRevenue.toFixed(2)));
    $('#totalProjectedCost').text(formatIndianRupee(totalLeadCost.toFixed(2)));
    $('#totalProjectedProfit').text(formatIndianRupee(netProfit.toFixed(2)));
    $('#totalProjectedROI').text(roi.toFixed(2));

    const actualLeads = $('#actual_lead_value').text();
    const actualAppointmentsBooked = $('#appointment_booked_count').text();
    const actualShowUps = $('#actual_show_up_rate_value').text();
    const actualSalesClosure = $('#actual_sales_closure_rate_value').text();
    const actualLeadCost = $('#actual_lead_cost').text();
    const actualAppointmentBookedCost = actualLeadCost / actualAppointmentsBooked;
    const actualShowUpRateCost = actualLeadCost / actualShowUps;
    const actualSalesClosureCost = actualLeadCost / actualSalesClosure;

    $('#actual_appointment_booked_cost').text(formatIndianRupee(actualAppointmentBookedCost.toFixed(2)));
    $('#actual_show_up_rate_cost').text(formatIndianRupee(actualShowUpRateCost.toFixed(2)));
    $('#actual_sales_closure_cost').text(formatIndianRupee(actualSalesClosureCost.toFixed(2)));

    

    // Calculate and update actual metrics
    const totalActualRevenue = parseFloat($('#total_actual_revenue').val());
    const totalActualCost = actualLeadCost;
    const totalActualProfit = totalActualRevenue - totalActualCost;
    const totalActualROI = totalActualCost > 0 ? totalActualProfit / totalActualCost : 0;

    // Calcuate the actual rates and set it in the html
    const actualAppointmentBookedRate = (actualAppointmentsBooked / actualLeads) * 100;
    const actualShowUpRate = (actualShowUps / actualAppointmentsBooked) * 100;
    const actualSalesClosureRate = (actualSalesClosure / actualShowUps) * 100;

    document.getElementById('totalActualRevenue').textContent = formatIndianRupee(totalActualRevenue.toFixed(2));
    document.getElementById('totalActualCost').textContent = formatIndianRupee(totalActualCost);
    document.getElementById('totalActualProfit').textContent = formatIndianRupee(totalActualProfit.toFixed(2));
    document.getElementById('totalActualROI').textContent = totalActualROI.toFixed(2);
    document.getElementById('actual_appointment_booked_rate').textContent = actualAppointmentBookedRate.toFixed(2);
    document.getElementById('actual_show_up_rate').textContent = actualShowUpRate.toFixed(2);
    document.getElementById('actual_sales_closure_rate').textContent = actualSalesClosureRate.toFixed(2);

    // Apply color-coding for leads
    setColorBasedOnComparison(actualLeads, leadGenerationProjection, leadGenerationGoal, '#actual_lead_value');
    setColorBasedOnComparison(totalLeadCost, actualLeadCost, actualLeadCost, '#actual_lead_cost');

    // Apply color-coding for appointments booked
    setColorBasedOnComparison(actualAppointmentsBooked, appointmentCountProjection, appointmentCountGoal, '#appointment_booked_count');
    setColorBasedOnComparison(appointmentCost, actualAppointmentBookedCost, actualAppointmentBookedCost, '#actual_appointment_booked_cost');

    // Apply color-coding for show-ups
    setColorBasedOnComparison(actualShowUps, attendedCountProjection, attendedCountGoal, '#actual_show_up_rate_value');
    setColorBasedOnComparison(attendedCost, actualShowUpRateCost, actualShowUpRateCost, '#actual_show_up_rate_cost');

    // Apply color-coding for sales closure
    setColorBasedOnComparison(actualSalesClosure, salesCountProjection, salesCountGoal, '#actual_sales_closure_rate_value');
    setColorBasedOnComparison(saleCost, actualSalesClosureCost, actualSalesClosureCost, '#actual_sales_closure_cost');

    setColorBasedOnComparison(totalActualRevenue, totalRevenue, totalRevenue, '#totalActualRevenue');
    setColorBasedOnComparison(totalCost, totalActualCost, totalActualCost, '#totalActualCost');
    setColorBasedOnComparison(totalActualProfit, netProfit, netProfit, '#totalActualProfit');
    setColorBasedOnComparison(totalActualROI, roi, roi, '#totalActualROI');
    setColorBasedOnComparison(actualAppointmentBookedRate, bookingRateProjection, bookingRateGoal, '#actual_appointment_booked_rate');
    setColorBasedOnComparison(showUpRateProjection, showUpRateGoal,actualShowUpRate, '#actual_show_up_rate');
    setColorBasedOnComparison(actualSalesClosureRate, closeRateProjection, closeRateGoal, '#actual_sales_closure_rate');
}

// Color-coding logic for actual vs projected vs goal values
function setColorBasedOnComparison(actualValue, projectedValue, goalValue, elementId) {
    const $element = $(elementId);
    if (actualValue >= goalValue) {
        $element.css('color', 'darkgreen');
    } else if (actualValue >= projectedValue) {
        $element.css('color', 'green');
    } else {
        $element.css('color', 'red');
    }
}

$(document).ready(function() {
    calculateMetrics();
    $('input').on('input', calculateMetrics);
});
