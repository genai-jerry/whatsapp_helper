function loadSalesProjection() {
    const employeeId = $('#employee-dropdown').val();
    const month = $('#month').val();
    const year = $('#year').val();

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
                $('#leadCount').val(response.projection.total_call_slots);
                $('#closeRate').val(response.projection.closure_percentage_projected);
                $('#appointment_booked_projection').val(response.projection.appointment_booked_projection);
                $('#show_up_rate_projection').val(response.projection.show_up_rate_projection);
                $('#costPerLead').val(response.projection.cost_per_lead);
                $('#averageSaleValue').val(response.projection.sale_price);
                
                // Update goal fields
                $('#appointment_booked_goal').val(response.projection.appointment_booked_goal);
                $('#show_up_rate_goal').val(response.projection.show_up_rate_goal);
                
                // Trigger calculation
                calculateMetrics();
            } else {
                // Clear form fields if no projection data is found
                $('#leadCount').val('');
                $('#closeRate').val('');
                $('#appointment_booked_projection').val('');
                $('#show_up_rate_projection').val('');
                $('#costPerLead').val('');
                $('#averageSaleValue').val('');
                $('#appointment_booked_goal').val('');
                $('#show_up_rate_goal').val('');
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
    const totalCallSlots = parseInt($('#sales_slots_possible').val()) || 0;
    
    // Calculate goal values
    const bookingRateGoal = parseFloat($('#appointment_booked_goal').val()) || 0;
    const showUpRateGoal = parseFloat($('#show_up_rate_goal').val()) / 100 || 0;
    const closeRateGoal = parseFloat($('#close_rate_goal').val()) / 100 || 0;
    const leadGenerationGoal = bookingRateGoal > 0 ? Math.round((totalCallSlots *100) / bookingRateGoal) : 0;
    const appointmentCountGoal = bookingRateGoal > 0 ? Math.round(leadGenerationGoal * (bookingRateGoal / 100)) : 0;
    const attendedCountGoal = showUpRateGoal > 0 ? Math.round(appointmentCountGoal * showUpRateGoal) : 0;
    const salesCountGoal = closeRateGoal > 0 ? Math.round(attendedCountGoal * closeRateGoal) : 0;

    $('#appointment_booked_goal_value').text(appointmentCountGoal);
    $('#show_up_rate_goal_value').text(attendedCountGoal);
    $('#sales_goal_closure_rate_value').text(salesCountGoal);
    // Update the lead generation goal input field
    $('#lead_generation_goal').val(leadGenerationGoal);

    // Calculate goal values
    const bookingRateProjection = parseFloat($('#appointment_booked_projection').val()) || 0;
    const showUpRateProjection = parseFloat($('#show_up_rate_projection').val()) / 100 || 0;
    const closeRateProjection = parseFloat($('#close_rate_projection').val()) / 100 || 0;
    const leadGenerationProjection = bookingRateProjection > 0 ? Math.round((totalCallSlots *100) / bookingRateProjection) : 0;
    const appointmentCountProjection = bookingRateProjection > 0 ? Math.round(leadGenerationProjection * (bookingRateProjection / 100)) : 0;
    const attendedCountProjection = showUpRateProjection > 0 ? Math.round(appointmentCountProjection * showUpRateProjection) : 0;
    const salesCountProjection = closeRateProjection > 0 ? Math.round(attendedCountProjection * closeRateProjection) : 0;

    $('#appointment_booked_projection_value').text(appointmentCountProjection);
    $('#show_up_rate_projection_value').text(attendedCountProjection);
    $('#sales_projected_closure_rate_value').text(salesCountProjection);
    // Update the lead generation goal input field
    $('#lead_generation_projection').val(leadGenerationProjection);
    const costPerLead = parseFloat($('#costPerLead').val()) || 0;
    const averageSaleValue = parseFloat($('#averageSaleValue').val()) || 0;
    
    const totalLeadCost = leadGenerationGoal * costPerLead;
    const appointmentCost = appointmentCountProjection > 0 ? totalLeadCost / appointmentCountProjection : 0;
    const attendedCost = attendedCountProjection > 0 ? totalLeadCost / attendedCountProjection : 0;
    const saleCost = salesCountProjection > 0 ? totalLeadCost / (salesCountProjection > 0 ? salesCountProjection : 1) : 0;

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

    const actualLeads = $('#total_lead_value').text();
    const actualAdLeads = $('#ad_lead_value').text();
    const actualAppointmentsBooked = $('#appointment_booked_count').text();
    const totalAppointmentsScheduled = $('#total_appointments_scheduled_value').text();
    const actualShowUps = $('#actual_show_up_rate_value').text();
    const actualSalesClosure = $('#actual_sales_closure_rate_value').text();
    const actualLeadCost = $('#actual_lead_cost').text();
    const actualAppointmentBookedCost = actualAppointmentsBooked > 0 ? actualLeadCost / actualAppointmentsBooked : 0;
    const actualShowUpRateCost = actualShowUps > 0 ? actualLeadCost / actualShowUps : 0;
    const actualSalesClosureCost = actualSalesClosure > 0 ? actualLeadCost / (actualSalesClosure > 0 ? actualSalesClosure : 1) : 0;

    $('#actual_appointment_booked_cost').text(formatIndianRupee(actualAppointmentBookedCost.toFixed(2)));
    $('#actual_show_up_rate_cost').text(formatIndianRupee(actualShowUpRateCost.toFixed(2)));
    $('#actual_sales_closure_cost').text(formatIndianRupee(actualSalesClosureCost.toFixed(2)));

    

    // Calculate and update actual metrics
    const totalActualRevenue = parseFloat($('#total_actual_revenue').val()) || 0;
    const totalActualCost = actualLeadCost;
    const totalActualProfit = totalActualRevenue - totalActualCost;
    const totalActualROI = totalActualCost > 0 ? totalActualProfit / totalActualCost : 0;

    // Calcuate the actual rates and set it in the html
    const actualAppointmentBookedRate = (actualAppointmentsBooked / actualLeads) * 100;
    const actualShowUpRate = totalAppointmentsScheduled > 0 ? (actualShowUps / totalAppointmentsScheduled) * 100 : 0;
    const actualSalesClosureRate = actualShowUps > 0 ? (actualSalesClosure / actualShowUps) * 100 : 0;
    const actualCostPerLead = actualAdLeads > 0 ? actualLeadCost / actualAdLeads : 0;

    $('#totalActualRevenue').text(formatIndianRupee(totalActualRevenue.toFixed(2)));
    $('#totalActualCost').text(formatIndianRupee(totalActualCost));
    $('#totalActualProfit').text(formatIndianRupee(totalActualProfit.toFixed(2)));
    $('#totalActualROI').text(totalActualROI.toFixed(2));
    $('#actual_appointment_booked_rate').text(actualAppointmentBookedRate.toFixed(2));
    $('#actual_show_up_rate').text(actualShowUpRate.toFixed(2));
    $('#actual_sales_closure_rate').text(actualSalesClosureRate.toFixed(2));
    $('#actual_cost_per_lead').val(formatIndianRupee(actualCostPerLead.toFixed(2)));
    // Apply color-coding for leads
    setColorBasedOnComparison(actualLeads, leadGenerationProjection, leadGenerationGoal, '#total_lead_value');
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
